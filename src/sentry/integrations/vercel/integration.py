from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _


from sentry.integrations import (
    IntegrationInstallation,
    IntegrationFeatures,
    IntegrationProvider,
    IntegrationMetadata,
    FeatureDescription,
)
from sentry.pipeline import NestedPipelineView
from sentry.identity.pipeline import IdentityProviderPipeline
from sentry.utils.http import absolute_uri
from sentry.models import Project, ProjectKey
from sentry.utils.compat import map
from sentry.shared_integrations.exceptions import ApiError

from .client import VercelClient

DESCRIPTION = """
VERCEL DESC
"""

FEATURES = [
    FeatureDescription(
        """
        DEPLOYMENT DESCRIPTION
        """,
        IntegrationFeatures.DEPLOYMENT,
    ),
]


metadata = IntegrationMetadata(
    description=DESCRIPTION.strip(),
    features=FEATURES,
    author="The Sentry Team",
    noun=_("Installation"),
    issue_url="https://github.com/getsentry/sentry/issues/new?title=Vercel%20Integration:%20&labels=Component%3A%20Integrations",
    source_url="https://github.com/getsentry/sentry/tree/master/src/sentry/integrations/vercel",
    aspects={},
)


class VercelIntegration(IntegrationInstallation):
    def get_organization_config(self):
        metadata = self.model.metadata
        vercel_client = VercelClient(metadata["access_token"], metadata.get("team_id"))
        # TODO: add try/catch if we get API failure
        vercel_projects = [
            {"value": p["id"], "label": p["name"]} for p in vercel_client.get_projects()
        ]

        proj_fields = ["id", "platform", "name", "slug"]
        sentry_projects = map(
            lambda proj: {key: proj[key] for key in proj_fields},
            (
                Project.objects.filter(organization_id=self.organization_id)
                .order_by("slug")
                .values(*proj_fields)
            ),
        )

        fields = [
            {
                "name": "project_mappings",
                "type": "project_mapper",
                "mappedDropdown": {
                    "items": vercel_projects,
                    "placeholder": "Select a Vercel Project",  # TOOD: add translation
                },
                "sentryProjects": sentry_projects,
            }
        ]

        return fields

    def update_organization_config(self, data):
        # data = {"project_mappings": [[sentry_project_id, vercel_project_id]]}

        metadata = self.model.metadata
        vercel_client = VercelClient(metadata["access_token"], metadata.get("team_id"))
        config = self.org_integration.config
        sentry_project_id = data["project_mappings"][-1][0]
        vercel_project_id = data["project_mappings"][-1][1]
        sentry_project = Project.objects.get(id=sentry_project_id)
        sentry_project_dsns = ProjectKey.objects.filter(project=sentry_project).all()
        enabled_dsns = [dsn for dsn in sentry_project_dsns if dsn.is_active]
        if enabled_dsns:  # in case there are no enabled DSNs
            sentry_project_dsn = enabled_dsns[0].get_dsn(public=True)
        else:
            raise
        try:
            self.create_secret(
                vercel_client, vercel_project_id, "SENTRY_ORG", sentry_project.organization.slug
            )
        except Exception:
            raise

        try:
            self.create_secret(
                vercel_client, vercel_project_id, "SENTRY_PROJECT", sentry_project.slug
            )
        except Exception:
            raise

        try:
            self.create_secret(
                vercel_client, vercel_project_id, "NEXT_PUBLIC_SENTRY_DSN", sentry_project_dsn
            )
        except Exception:
            raise

        config.update(data)
        self.org_integration.update(config=config)

    def get_env_vars(self, client, vercel_project_id):
        return client.get(path=client.GET_ENV_VAR_URL % vercel_project_id)

    def get_secret(self, client, name):
        try:
            exists = True
            client.get(path=client.GET_SECRET_URL % name)
        except ApiError as e:
            if e.code == 404:
                exists = False
            else:
                raise
        return exists

    def env_var_already_exists(self, client, vercel_project_id, name):
        return len(
            filter(
                lambda env_var: env_var["key"] == name,
                self.get_env_vars(client, vercel_project_id)["envs"],
            )
        )

    def create_secret(self, client, vercel_project_id, name, value):
        secret = None
        if not self.get_secret(client, name):
            secret = client.post(path=client.SECRETS_URL, data={"name": name, "value": value})[
                "uid"
            ]
        if secret is not None and not self.env_var_already_exists(client, vercel_project_id, name):
            self.create_env_var(client, vercel_project_id, name, secret)

    def create_env_var(self, client, vercel_project_id, key, value):
        try:
            client.post(
                path=client.ENV_VAR_URL % vercel_project_id,
                data={"key": key, "value": value, "target": "production"},
            )
        except ApiError:
            raise


class VercelIntegrationProvider(IntegrationProvider):
    key = "vercel"
    name = "Vercel"
    requires_feature_flag = True
    metadata = metadata
    integration_cls = VercelIntegration
    features = frozenset([IntegrationFeatures.DEPLOYMENT])
    oauth_redirect_url = "/extensions/vercel/configure/"

    def get_pipeline_views(self):
        identity_pipeline_config = {"redirect_url": absolute_uri(self.oauth_redirect_url)}

        identity_pipeline_view = NestedPipelineView(
            bind_key="identity",
            provider_key=self.key,
            pipeline_cls=IdentityProviderPipeline,
            config=identity_pipeline_config,
        )

        return [identity_pipeline_view]

    def build_integration(self, state):
        data = state["identity"]["data"]
        access_token = data["access_token"]
        team_id = data.get("team_id")
        client = VercelClient(access_token, team_id)

        if team_id:
            external_id = team_id
            installation_type = "team"
            team = client.get_team()
            name = team["name"]
        else:
            external_id = data["user_id"]
            installation_type = "user"
            user = client.get_user()
            name = user["name"]

        integration = {
            "name": name,
            "external_id": external_id,
            "metadata": {
                "access_token": access_token,
                "installation_id": data["installation_id"],
                "installation_type": installation_type,
            },
        }

        return integration
