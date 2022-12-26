import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders loader container', () => {
  render(<App apiInfoUrl="" />);
  const linkElement = screen.getByText(/Loading/i);
  expect(linkElement).toBeInTheDocument();
});
