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

import { render, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';

import { routes } from '@/routes';
import server from '@/testing/server';
import { generateCodeVerifier } from '@/tool/pkce';
import { tokenUrls } from '@/urls';
import { getManyUuids, setManyItems } from '@/util';

import AuthorizeCallback from '../AuthorizeCallback';

describe('AuthorizeCallback view', () => {
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
    const { baseElement: root } = render(<AuthorizeCallback />);

    // Then
    expect(root).toBeTruthy();
  });

  it('renders the error for an invalid callback', async () => {
    // Given
    const expectedError = 'Invalid authorization callback.';

    // When
    const { findByTestId } = render(<AuthorizeCallback />);

    // Then
    const error = await findByTestId('error');

    expect(error).toHaveTextContent(expectedError);
  });

  it('renders the error for a failed request', async () => {
    // Given
    const expectedError = 'This is a backend error.';

    server.use(
      http.post(tokenUrls.issue, () =>
        HttpResponse.json({ detail: expectedError }, { status: 400 })
      )
    );

    const [clientId, code, state] = getManyUuids(3);
    const codeVerifier = generateCodeVerifier();

    mockParams.set('code', code);
    mockParams.set('state', state);
    setManyItems({ clientId, codeVerifier, state });

    // When
    const { findByTestId } = render(<AuthorizeCallback />);

    // Then
    expect(calledEndpoints).toEqual([tokenUrls.issue]);
    expect(mockNavigate).not.toHaveBeenCalled();

    const error = await findByTestId('error');
    expect(error).toHaveTextContent(expectedError);
  });

  it('navigates to main after a successful authorization', async () => {
    // Given
    server.use(
      http.post(tokenUrls.issue, () => new HttpResponse(null, { status: 201 }))
    );

    const [clientId, code, state] = getManyUuids(3);
    const codeVerifier = generateCodeVerifier();

    mockParams.set('code', code);
    mockParams.set('state', state);
    setManyItems({ clientId, codeVerifier, state });

    // When
    render(<AuthorizeCallback />);

    // Then
    await waitFor(() => expect(calledEndpoints).toEqual([tokenUrls.issue]));
    expect(mockNavigate).toHaveBeenCalledWith(routes.main.root);
  });
});
