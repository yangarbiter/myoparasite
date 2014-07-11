all: click.c
	gcc -o click -Dxdo_click=xdo_click_window click.c -lxdo
