#!/bin/bash
export LD_LIBRARY_PATH=/usr/lib:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
streamlit run app.py
