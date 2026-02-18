NAME = a_maze_ing.py
VENV = .venv

all: run
install:
	pip install --upgrade pip build
	python3 -m build --sdist
	cp dist/mazegen-*.tar.gz mazegen.tar.gz
	pip install textual
	pip install -e .

build:
	python3 -m build

clean:
	@rm -rf dist/ build/ *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
	rm -f mazegen.tar.gz

run:
	python3 $(NAME) config.txt

re: fclean install

.PHONY: all install build clean fclean run re