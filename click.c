#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
#include <xdo.h>

/*
int main () {
	xdo_t* xdo = xdo_new (NULL);
	if (xdo == NULL) {
		perror ("xdo_new");
		return 1;
	}

	int c;
	while ((c = getchar ()) != EOF) {
		int button = c - '0';
		if (!isdigit (c)) {
			continue;
		}
		xdo_click (xdo, CURRENTWINDOW, button);
	}

	return 0;
}
*/

static xdo_t *xdo = NULL;

int myoparasite_mouse_init (void) {
	xdo = xdo_new (NULL);
	if (xdo == NULL) {
		return -1;
	}
	return 0;
}

void myoparasite_mouse_click (int action) {
	switch (action) {
		case 1: case 2: case 3: case 4: case 5:
			xdo_click (xdo, CURRENTWINDOW, button);
			break;
	}
}
