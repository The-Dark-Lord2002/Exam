/* خروجی همهٔ مثال‌ها، تمرین‌ها و آزمون فصل ۲ برنامه‌سازی (شرط، switch، حلقه، break/continue).
   اجرا:  gcc -std=c11 -w "فصل-02.c" -o f2 && ./f2 */
#include <stdio.h>
int main(void) {
  /* درس ۱: if */
  { int a = 0, b = 1; printf("L1a: "); if (a) if (b) printf("X"); else printf("Y"); printf("Z\n"); }
  { int x = 3; printf("L1b: "); if (x > 5); printf("A\n"); }
  { int x = 0; printf("L1c: "); if (x = 5) printf("%d\n", x); }
  { int x = -2; printf("L1d: %s\n", x ? "true" : "false"); }
  /* درس ۲: switch */
  { int k = 2, s = 0; switch (k) { case 1: s += 1; case 2: s += 2; case 3: s += 3; break; case 4: s += 4; default: s += 10; } printf("L2a: %d\n", s); }
  { int k = 7, s = 0; switch (k) { default: s += 10; case 1: s += 1; break; case 2: s += 2; } printf("L2b: %d\n", s); }
  { int k = 4, s = 0; switch (k) { case 1: s += 1; case 2: s += 2; case 3: s += 3; break; case 4: s += 4; default: s += 10; } printf("L2c: %d\n", s); }
  /* درس ۳: حلقه */
  { int i = 10; printf("L3a: "); do { printf("%d ", i); i++; } while (i < 5); printf("\n"); }
  { int i; for (i = 0; i < 5; i++); printf("L3b: %d\n", i); }
  { int i, c = 0; for (i = 1; i <= 100; i += 3) c++; printf("L3c: %d %d\n", c, i); }
  { int i = 0; printf("L3d: "); while (i++ < 3) printf("%d ", i); printf("| %d\n", i); }
  { int i = 5; printf("L3e: "); while (i --> 0) printf("%d", i); printf("\n"); }
  { int i, j, c = 0; for (i = 0, j = 10; i < j; i += 2, j -= 3) c++; printf("L3f: %d\n", c); }
  { printf("L3g: "); for (char c = 'a'; c <= 'e'; c += 2) printf("%c", c); printf("\n"); }
  { int c = 0; for (int i = 0; i < 4; i++) for (int j = i; j < 4; j++) c++; printf("L3h: %d\n", c); }
  /* درس ۴: break / continue */
  { int s = 0; for (int i = 1; i <= 10; i++) { if (i % 2 == 0) continue; if (i > 7) break; s += i; } printf("L4a: %d\n", s); }
  { int c = 0; for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) { if (j == 1) break; c++; } printf("L4b: %d\n", c); }
  { int s = 0, i = 0; while (i < 10) { i++; if (i % 3 == 0) continue; s += i; } printf("L4c: %d\n", s); }
  /* آزمون فصل */
  { int x = 5, y = 10; if (x > y) if (y > 0) x = 1; else x = 2; printf("Q1: %d\n", x); }
  { int n = 3, r = 0; switch (n) { case 1: r++; case 3: r += 3; case 5: r += 5; default: r += 100; } printf("Q2: %d\n", r); }
  { int i = 0, s = 0; do { s += i; i += 2; } while (i < 0); printf("Q3: %d %d\n", s, i); }
  { int c = 0; for (int i = 1; i <= 20; i *= 3) c++; printf("Q4: %d\n", c); }
  { int s = 0; for (int i = 0; i < 10; i++) { if (i == 2) continue; if (i == 6) break; s += i; } printf("Q5: %d\n", s); }
  { int i = 10; while (i-- > 7); printf("Q6: %d\n", i); }
  { int c = 0; for (int i = 0; i < 5; i++) for (int j = 0; j < i; j++) if ((i + j) % 2) c++; printf("Q7: %d\n", c); }
  { int x = -4, r = 0; switch (x % 3) { case 1: r = 1; break; case 2: r = 2; break; case -1: r = 3; break; default: r = 4; } printf("Q8: %d\n", r); }
  { int i, j, c = 0; for (i = 0, j = 10; i < j; i += 2, j -= 2) c++; printf("Q9: %d %d %d\n", c, i, j); }
  { int n = 0; for (int i = 1; i <= 3; i++) for (int j = 1; j <= 3; j++) { if (j == i) continue; if (j > i) break; n += 10 * i + j; } printf("Q10: %d\n", n); }
  return 0;
}
