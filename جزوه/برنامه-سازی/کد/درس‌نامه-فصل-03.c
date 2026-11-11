#include <stdio.h>
#define SQ(x) x*x
int sq(int n) { return n * n; }
void hello(int k) { printf("hi%d ", k); }
void twice(int v) { v = v * 2; printf("in:%d ", v); }
void f(void) { int a = 0; static int s = 0; a++; s++; printf("%d%d ", a, s); }
int main(void){
  int a = sq(3) + sq(2); printf("%d\n", a);
  hello(1); hello(2); printf("\n");
  int x = 4; twice(x); printf("out:%d\n", x);
  f(); f(); printf("\n");
  int m = 7; printf("%d %d\n", m > 5 ? 1 : 0, m % 2 == 0 ? m : -m);
  printf("%d\n", SQ(2+1));
  return 0;
}
