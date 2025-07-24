// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom'
    );

  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

import { render, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';

import { routes } from '@/routes';
import server from '@/testing/server';
import { tokenUrls } from '@/urls';

import Main from '../Main';

describe('Main view', () => {
  const calledEndpoints: string[] = [];

  beforeAll(() => {
    server.listen();

    server.events.on('request:start', ({ request }) =>
      calledEndpoints.push(request.url)
    );
  });

  beforeEach(() => {
    server.resetHandlers();

    calledEndpoints.length = 0;
    mockNavigate.mockClear();
  });

  afterAll(() => {
    server.close();
  });

  it('renders something', () => {
    // Given
    server.use(
      http.post(
        tokenUrls.refresh,
        () => new HttpResponse(null, { status: 201 })
      )
    );

    // When
    const { baseElement: root } = render(<Main />);

    // Then
    expect(root).toBeTruthy();
  });

  it('navigates to home when there is no valid refresh token', async () => {
    // Given
    server.use(
      http.post(
        tokenUrls.refresh,
        () => new HttpResponse(null, { status: 400 })
      )
    );

    // When
    render(<Main />);

    // Then
    await waitFor(() => expect(calledEndpoints).toEqual([tokenUrls.refresh]));
    expect(mockNavigate).toHaveBeenCalledWith(routes.home.root);
  });

  it('does not navigate when there is a valid refresh token', async () => {
    // Given
    server.use(
      http.post(
        tokenUrls.refresh,
        () => new HttpResponse(null, { status: 201 })
      )
    );

    // When
    render(<Main />);

    // Then
    await waitFor(() => expect(calledEndpoints).toEqual([tokenUrls.refresh]));
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
