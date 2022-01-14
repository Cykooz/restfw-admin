import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

test('renders loader container', () => {
  const { getByText } = render(<App apiInfoUrl="" />);
  const loadingElement = getByText(/Loading/i);
  expect(loadingElement).toBeInTheDocument();
});
