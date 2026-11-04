/* خروجی همهٔ مثال‌ها، تمرین‌ها و آزمون فصل ۱ برنامه‌سازی.
   اجرا:  gcc -std=c11 -w "فصل-01.c" -o f1 && ./f1
   هر خط با برچسب درس (L1..L4) یا سؤال آزمون (Q1..Q10) شروع می‌شود. */
#include <stdio.h>
int main(void){
  /* lesson 1 */
  printf("L1a: %d %d %d\n", 'A', 'a' - 'A', '7' - '0');
  { unsigned char c = 250; c = c + 10; printf("L1b: %d\n", c); }
  printf("L1c: %zu %zu\n", sizeof(char), sizeof('A'));
  { unsigned int u = 0; u = u - 1; printf("L1d: %u\n", u); }
  { int x = 7; size_t s = sizeof(x++); printf("L1e: %zu %d\n", s, x); }
  { unsigned char c = 255; c++; printf("L1f: %d\n", c); }
  { unsigned char uc = 300; printf("L1g: %d\n", uc); }
  printf("L1h: %zu %zu %zu %zu\n", sizeof(short), sizeof(int), sizeof(long), sizeof(double));
  /* lesson 2 */
  printf("L2a: %d %d %d %d\n", -7/2, -7%2, 7%-2, 7/-2);
  { int i=5; int j = i++ + 2; printf("L2b: %d %d\n", i, j); int k = ++i * 2; printf("L2c: %d %d\n", i, k); }
  { int a=17,b=5; printf("L2d: %d %d\n", a/b*b + a%b, a % b * 2); }
  { int a=2; a *= 3 + 4; printf("L2e: %d\n", a); }
  /* lesson 3 */
  { int a=3,b=4,c=5; printf("L3a: %d %d\n", a < b < c, c > b > a); }
  { int x = 6 & 3 == 3; printf("L3b: %d\n", x); }
  { int i=0,j=0; if (i++ && j++) ; printf("L3c: %d %d\n", i, j); if (i++ || j++) ; printf("L3d: %d %d\n", i, j); }
  { int a = (1, 2, 3); printf("L3e: %d\n", a); }
  { int x = 5; x = x > 3 ? x << 1 : x >> 1; printf("L3f: %d\n", x); }
  printf("L3g: %d %d\n", !5 == 0, 1 << 2 + 1);
  { int x = 0; if (x = 0) printf("L3h: in\n"); else printf("L3h: else\n"); }
  /* lesson 4 */
  { double d = 5/2; printf("L4a: %f %.1f %.1f\n", d, (double)5/2, (double)(5/2)); }
  printf("L4b: %s\n", (-1 < 1u) ? "yes" : "no");
  printf("L4c: %d %d\n", (int)-2.7, (int)2.7);
  { float f = 0.1; printf("L4d: %s\n", f == 0.1 ? "equal" : "not equal"); }
  { char c = 'A' + 2; printf("L4e: %c\n", c); }
  { int x = 'a' + 1.5; printf("L4f: %d\n", x); }
  printf("L4g: %.1f %.1f\n", 3/2*2.0, 3*2.0/2);
  /* chapter test */
  { int a = 10, b = 3; printf("Q1: %d %d\n", a / b, -a % b); }
  { int x = 5, y = 0; if (x > 3 || ++y) x++; printf("Q2: %d %d\n", x, y); }
  { int a = 1, b = 2, c = 3; printf("Q3: %d\n", a < b < c == c > b > a); }
  { unsigned int u = 1; int i = -1; printf("Q4: %s\n", i < u ? "less" : "not less"); }
  { double d = 7 / 2 + 7 / 2.0; printf("Q5: %.1f\n", d); }
  { int x = 0x0F; printf("Q6: %d\n", x & 0x3C | 1 << 4); }
  { int i = 3; int j = sizeof(i++) + i; printf("Q7: %d\n", j); }
  { char c = 'B'; c = c + ('a' - 'A'); printf("Q8: %c %d\n", c, c - 'a'); }
  { int a = 5, b; b = (a++, a * 2); printf("Q9: %d %d\n", a, b); }
  { int k = 0; int r = (k = 3) && (k = 0) || (k = 5); printf("Q10: %d %d\n", r, k); }
  return 0;
}
