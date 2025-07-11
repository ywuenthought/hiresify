// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { LinkBaseProps } from '@mui/material';
import { Link } from '@mui/material';

import { buildRegisterUserUrl } from '@/tool/url';

export default function RegisterLink(props: LinkBaseProps) {
  // Generate the full registration URL.
  const registerUrl = buildRegisterUserUrl();

  return (
    <Link
      fontWeight="bold"
      href={registerUrl.toString()}
      rel="noopener noreferrer"
      underline="hover"
      target="_parent"
      variant="subtitle1"
      {...props}
    >
      Register
    </Link>
  );
}
