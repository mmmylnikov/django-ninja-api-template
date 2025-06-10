ifneq (,$(wildcard .env))
  $(info Found .env file.)
  include .env
  export
endif

style_wps:
	flake8 . --select=WPS

style_ruff:
	ruff check .

format_ruff:
	ruff format .

style:
	make format_ruff style_ruff style_wps

types:
	mypy ./backend

check:
	make style types

debug:
	# open http://$(DEBUG_HOST):$(DEBUG_PORT)
	./backend/manage.py runserver $(DEBUG_HOST):$(DEBUG_PORT)

migrate:
	./backend/manage.py makemigrations
	./backend/manage.py migrate

initdata:
	./backend/manage.py initdata

celery:
	cd backend && celery -A config worker -l info 

celery_beat:
	cd backend && celery -A config beat

celery_flower:
	cd backend && celery -A config flower

notify_build_proto:
	cd notify_grpc_service && python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notyfy.proto