# ---------------------------------------------------------
# [  INCLUDES  ]
# override to whatever works on your system

PIPENV := pipenv

include ./Makefile.in.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# override to whatever works on your system

WSGI_APPLICATION := main.main:app
LOCAL_RUN := $(PYTHON) -m main.app

include ./Makefile.targets.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# keep your targets here

.PHONY: run
run:
	$(RUN) uvicorn main.main:app --reload --workers 1 --port 8888

