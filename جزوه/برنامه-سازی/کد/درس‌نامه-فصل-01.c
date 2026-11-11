#include <stdio.h>
int main(void){
  int a = 3, b = 4;
  a = a + b; b = a - b; a = a - b;
  printf("1: %d %d\n", a, b);
  int x = 2, y = 5; x = y; y = x; printf("2: %d %d\n", x, y);
  printf("3: "); printf("%d%d", 1, 2); printf("\n");
  printf("4: %f %.2f %.1f\n", 2.5, 2.5, 2.25);
  printf("5: %d %c %d %d\n", 'A', 65, '9'-'0', 'z'-'a');
  unsigned char u = 255; u++; printf("6: %d\n", u);
  int i = 5; printf("7: %d ", i++); printf("%d\n", i);
  printf("8: %d %d %d %d\n", 2 + 3 * 4, (2 + 3) * 4, 10 - 4 - 3, 2 * 3 % 4);
  printf("9: %d %d %f %f\n", 7/2, -7/2, 7/2.0, (double)(7/2));
  int t = 10; t += 2 * 3; printf("10: %d\n", t);
  int n = 0; int r = (n != 0) && (10 / n > 1); printf("11: %d\n", r);
  printf("12: %d %d\n", 9 % 4, -9 % 4);
  return 0;
}
