# -*- coding: utf-8 -*-
"""Prima configurazione di questo brain: le tue macroaree e, se vuoi, un training.

La logica vive nel motore (tools/onboarding.py), una volta sola; questo file e' solo
la porta d'ingresso per chi apre lo scheletro.
  python onboarding.py                         interattivo
  python onboarding.py --aree "a,b" --training nessuno
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.onboarding import main  # noqa: E402

if __name__ == "__main__":
    main()
