// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Logout } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

import { routes, tokenUrls } from '@/const';
import { buildRevokeTokenFormData } from '@/tool/url';
import { mustGet } from '@/util';

export default function LogoutButton(props: ButtonProps) {
  const navigate = useNavigate();

  const handleClick = async () => {
    const refreshToken = mustGet('refreshToken');
    const formData = buildRevokeTokenFormData({ refreshToken });

    await fetch(tokenUrls.issue, {
      body: formData,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      method: 'POST',
    });

    // Reset the session storage.
    sessionStorage.clear();

    // Navigate to home after a logout.
    navigate(routes.home.root);
  };

  return (
    <Button
      color="primary"
      fullWidth
      size="large"
      startIcon={<Logout />}
      variant="text"
      onClick={handleClick}
      {...props}
    >
      Log Out
    </Button>
  );
}
