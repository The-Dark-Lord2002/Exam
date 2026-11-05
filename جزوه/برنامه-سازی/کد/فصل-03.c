/* خروجی همهٔ مثال‌ها، تمرین‌ها و آزمون فصل ۳ برنامه‌سازی (تابع، ارسال پارامتر، حوزه، static، ماکرو).
   اجرا:  gcc -std=c11 -w "فصل-03.c" -o f3 && ./f3 */
#include <stdio.h>
#define SQ(x) x*x
#define SQ2(x) ((x)*(x))
#define DOUBLE(x) x + x
#define MAX(a,b) ((a) > (b) ? (a) : (b))
void swap_v(int a, int b) { int t = a; a = b; b = t; }
void swap_p(int *a, int *b) { int t = *a; *a = *b; *b = t; }
void set0(int a[]) { a[0] = 9; }
size_t sz(int a[10]) { return sizeof(a); }
int counter(void) { static int c = 0; c++; return c; }
int fa(void) { int a = 0; static int s = 0; a++; s++; return a * 10 + s; }
int gx = 5;
void hx(void) { printf("%d ", gx); }
int gzero;
int f1(int n) { static int s = 1; s *= n; return s; }
void g2(int x) { x = x * 2; }
void g3(int *p) { *p = *p * 2; }
int x5 = 1;
int f5(void) { return x5 * 10; }
void z6(int a[], int n) { for (int i = 0; i < n; i++) a[i] = a[i] * i; }
int t7(void) { static int k = 10; return k--; }
int g8 = 0;
int h8(int v) { g8 += v; return g8; }
int main(void) {
  /* درس ۱ و ۲: ارسال پارامتر */
  { int x = 1, y = 2; swap_v(x, y); printf("L2a: %d %d\n", x, y); swap_p(&x, &y); printf("L2b: %d %d\n", x, y); }
  { int v[3] = {1, 2, 3}; set0(v); printf("L2c: %d\n", v[0]); }
  { int v[10]; printf("L2d: %zu %zu\n", sizeof(v), sz(v)); }
  /* درس ۳: حوزه و static */
  { counter(); counter(); printf("L3a: %d\n", counter()); }
  { fa(); fa(); printf("L3b: %d\n", fa()); }
  { int gx = 10; printf("L3c: "); hx(); { int gx = 20; printf("%d ", gx); } printf("%d\n", gx); }
  { printf("L3d: %d\n", gzero); }
  /* درس ۴: ماکرو */
  printf("L4a: %d %d %d %d\n", SQ(1+2), SQ2(1+2), 100 / SQ(5), 100 / SQ2(5));
  /* آزمون فصل */
  { f1(2); f1(3); printf("Q1: %d\n", f1(4)); }
  { int a = 5; g2(a); g2(a); printf("Q2: %d\n", a); }
  { int a = 5; g3(&a); g3(&a); printf("Q3: %d\n", a); }
  { printf("Q4: %d\n", 3 * DOUBLE(4)); }
  { int x5 = 2; printf("Q5: %d\n", f5() + x5); }
  { int v[4] = {5, 5, 5, 5}; z6(v, 4); printf("Q6: %d %d\n", v[0], v[3]); }
  { int s = 0; for (int i = 0; i < 3; i++) s += t7(); printf("Q7: %d\n", s); }
  { int a = h8(3); int b = h8(4); printf("Q8: %d %d %d\n", a, b, g8); }
  { for (int i = 0; i < 3; i++) { int a = 0; static int b = 0; a += i; b += i; if (i == 2) printf("Q9: %d %d\n", a, b); } }
  { int x = 5, y = 3; int m = MAX(x++, y); printf("Q10: %d %d\n", m, x); }
  return 0;
}
