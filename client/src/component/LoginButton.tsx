// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Login } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';

import { buildLoginUserUrl } from '@/tool/url';

export default function LoginButton(props: ButtonProps) {
  const loginUrl = buildLoginUserUrl();

  const handleClick = async () => {
    // Redirect to the login URL.
    window.location.href = loginUrl.toString();
  };

  return (
    <Button
      color="primary"
      fullWidth
      size="large"
      startIcon={<Login />}
      variant="contained"
      onClick={handleClick}
      {...props}
    >
      Get Started
    </Button>
  );
}
