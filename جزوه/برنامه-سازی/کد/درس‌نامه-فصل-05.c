#include <stdio.h>
#include <string.h>
int main(void){
  int a[5] = {10, 20, 30, 40, 50};
  int s = 0; for (int i = 0; i < 5; i++) s += a[i];
  printf("%d %d %d\n", a[0], a[4], s);
  int b[5] = {1, 2}; printf("%d %d %d\n", b[1], b[2], b[4]);
  int x = 5; int *p = &x; printf("%d ", *p); *p = 8; printf("%d\n", x);
  int *q = a; q++; printf("%d %d\n", *q, *(q+2));
  char t[] = "abc"; printf("%zu %zu %c %d\n", sizeof(t), strlen(t), t[1], t[3]);
  char u[] = "hello"; u[0] = 'j'; printf("%s %s\n", u, u + 2);
  return 0;
}
