// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const mockNavigate = vi.fn();
const mockParams = new URLSearchParams();

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom'
    );

  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: () => [mockParams],
  };
});

import { render } from '@testing-library/react';

import server from '@/testing/server';

import RegisterCallback from '../RegisterCallback';

describe('RegisterCallback view', () => {
  const calledEndpoints: string[] = [];

  beforeAll(() => {
    server.listen();

    server.events.on('request:start', ({ request }) =>
      calledEndpoints.push(request.url)
    );
  });

  beforeEach(() => {
    sessionStorage.clear();
    server.resetHandlers();

    calledEndpoints.length = 0;
    mockNavigate.mockClear();

    for (const key of mockParams.keys()) {
      mockParams.delete(key);
    }
  });

  afterAll(() => {
    server.close();
  });

  it('renders something', () => {
    // When
    const { baseElement: root } = render(<RegisterCallback />);

    // Then
    expect(root).toBeTruthy();
  });

  it('congratulates when the registration succeeded', () => {
    // When
    const { getByTestId } = render(<RegisterCallback />);

    // Then
    const success = getByTestId('success');
    expect(success).toHaveTextContent('Congratulations!');
  });
});
