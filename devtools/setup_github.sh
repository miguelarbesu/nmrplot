#!/usr/bin/env bash
# -*- coding: utf-8 -*-

printf "Creating GitHub repository..."
gh repo create nmrplot
git push --set-upstream origin main
