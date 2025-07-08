// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { LinkBaseProps } from '@mui/material';
import { Link } from '@mui/material';

import { buildRegisterUserUrl } from '@/tool/url';
import { getUuid4, setManyItems } from '@/util';

export default function RegisterLink(props: LinkBaseProps) {
  // Generate the register token.
  const registerToken = getUuid4();

  // Save the register token to be used later.
  setManyItems({ registerToken });

  // Generate the full registration URL.
  const registerUrl = buildRegisterUserUrl({ registerToken });

  return (
    <Link
      fontWeight="bold"
      href={registerUrl.toString()}
      rel="noopener noreferrer"
      underline="hover"
      target="_blank"
      variant="subtitle1"
      {...props}
    >
      Register
    </Link>
  );
}
