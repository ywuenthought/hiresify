# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the testing data to be used in tests elsewhere."""

import base64
import io

PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAA"
    "BHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAA"
    "AAd0SU1FB+MGBg8bCVyPYWgAAAAZdEVYdENvbW1lbnQAQ3Jl"
    "YXRlZCB3aXRoIEdJTVBXgQ4XAAABKElEQVQoz2NgGAWjgBEw"
    "QuD///9fBgYGJrAAKYHGJkY4ZgZGRqYDE2BgkMBgYgSRkZGZ"
    "gBxRi0CGQYGBgYGEVjYGJiYGLI4AFEShZIBwDYGhgYGMQLiw"
    "rAwNDZyANgSCiQRI2T2HgYGJkYO8nF6EMZJ6CSiZhgYGBv7D"
    "AYpJkwMkGRgYGBgbG/4CkRYBkYCNv/88YGBgaGWw1UwgUMwC"
    "IoAKmYAnMQAAAABJRU5ErkJggg=="
)

PNG_BYTES = base64.b64decode(PNG_BASE64)

PNG_STREAM = io.BytesIO(PNG_BYTES)
