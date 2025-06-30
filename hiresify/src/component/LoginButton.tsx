// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Login } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';

interface LoginButtonProps extends ButtonProps {
  loginUrl: string;
}

export default function LoginButton(props: LoginButtonProps) {
  const { loginUrl, ...rest } = props;

  const handleClick = () => {
    window.open(loginUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <Button
      color="primary"
      fullWidth
      size="large"
      startIcon={<Login />}
      variant="contained"
      onClick={handleClick}
      {...rest}
    >
      Log In
    </Button>
  );
}
