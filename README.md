# CoAgent – Self‑Repairing Diagnostic System

[![Agent Status](https://img.shields.io/badge/CoAgent-Healthy-brightgreen)](STATUS.md)

## Overview
CoAgent is a CMD‑based diagnostic and automation agent designed to run on Windows.  
It integrates Python modules for troubleshooting, automation, and web development, with built‑in self‑repair, logging, and GitHub integration.

## Features
- 🔧 **Self‑Repair Diagnostics**  
  Automatically checks directories, modules, and Python installation. Repairs missing folders or files with placeholders.

- 📜 **Logging System**  
  - `diagnostic.log` → full run details  
  - `repair.log` → concise list of repairs performed or required  

- 🛡️ **Status Badge**  
  Displays live health status in the README:  
  - ✅ Healthy (no errors)  
  - ❌ Issues (errors detected, repairs attempted)  

- 📂 **Modular Design**  
  Python modules for troubleshooting, fuel calculation, proposal drafting, and script generation.

- 🔄 **GitHub Integration**  
  Auto‑commit and push updates (optional). Keeps logs and badge status synced with the repository.

## Repository Structure
