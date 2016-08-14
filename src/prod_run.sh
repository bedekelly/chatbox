#!/bin/bash
gunicorn chatbox:app --workers 9 -k "eventlet"
