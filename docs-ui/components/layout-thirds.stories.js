import React from 'react';
import styled from '@emotion/styled';
import {storiesOf} from '@storybook/react';
import {withInfo} from '@storybook/addon-info';

import Button from 'app/components/button';
import ButtonBar from 'app/components/buttonBar';
import Breadcrumbs from 'app/components/breadcrumbs';
import * as Layout from 'app/components/layouts/thirds';

const crumbs = [
  {
    label: 'Issues',
    to: '',
  },
  {
    label: 'List',
    to: '',
  },
  {
    label: 'Detail',
    to: '',
  },
];

storiesOf('Layouts|Thirds', module)
  .add(
    '66/33 layout',
    withInfo('Two column layout with header & sidebar')(() => (
      <Container>
        <Layout.Header>
          <Heading>Some heading content</Heading>
        </Layout.Header>
        <Layout.LayoutBody>
          <Layout.Main>
            <h1>Content Region</h1>
            <p>Some text here</p>
          </Layout.Main>
          <Layout.Side>
            <h3>Sidebar content</h3>
          </Layout.Side>
        </Layout.LayoutBody>
      </Container>
    ))
  )
  .add(
    '66/33 with header controls',
    withInfo('Two column layout with header controls')(() => (
      <Container>
        <Layout.Header>
          <Layout.HeaderRegion>
            <Breadcrumbs crumbs={crumbs} />
            <Button>Top button</Button>
          </Layout.HeaderRegion>
          <Layout.HeaderRegion>
            <Heading>Some heading content</Heading>
            <ButtonBar gap={1}>
              <Button size="small">clicker</Button>
              <Button size="small">clicker</Button>
            </ButtonBar>
          </Layout.HeaderRegion>
        </Layout.Header>
        <Layout.LayoutBody>
          <Layout.Main>
            <h1>Content Region</h1>
            <p>Some text here</p>
          </Layout.Main>
          <Layout.Side>
            <h3>Sidebar content</h3>
          </Layout.Side>
        </Layout.LayoutBody>
      </Container>
    ))
  )
  .add(
    '66/33 with many header controls',
    withInfo('Two column layout with header controls')(() => (
      <Container>
        <Layout.Header>
          <Layout.HeaderRegion>
            <Breadcrumbs crumbs={crumbs} />
            <Button>Top button</Button>
          </Layout.HeaderRegion>
          <Layout.HeaderRegion>
            <Heading>Heading text</Heading>
            <ButtonBar gap={1}>
              <Button size="small">rollup</Button>
              <Button size="small">modify</Button>
              <Button size="small">create</Button>
              <Button size="small">update</Button>
              <Button size="small">delete</Button>
            </ButtonBar>
          </Layout.HeaderRegion>
        </Layout.Header>
        <Layout.LayoutBody>
          <Layout.Main>
            <h1>Content Region</h1>
            <p>Some text here</p>
          </Layout.Main>
          <Layout.Side>
            <h3>Sidebar content</h3>
          </Layout.Side>
        </Layout.LayoutBody>
      </Container>
    ))
  )
  .add(
    'single column mode',
    withInfo('Single column mode so we can hide the sidebar')(() => (
      <Container>
        <Layout.Header>
          <Layout.HeaderRegion>
            <Breadcrumbs crumbs={crumbs} />
            <Button>Top button</Button>
          </Layout.HeaderRegion>
          <Layout.HeaderRegion>
            <Heading>Some heading content</Heading>
            <ButtonBar gap={1}>
              <Button size="small">clicker</Button>
              <Button size="small">clicker</Button>
            </ButtonBar>
          </Layout.HeaderRegion>
        </Layout.Header>
        <Layout.LayoutBody>
          <Layout.Main fullWidth>
            <h1>Content Region</h1>
            <p>Some text here</p>
          </Layout.Main>
        </Layout.LayoutBody>
      </Container>
    ))
  );

const Container = styled('div')`
  background: #fbfbfc;
  margin: 16px;
  border: 1px solid ${p => p.theme.gray400};
`;

const Heading = styled('h2')`
  margin: 0;
`;
