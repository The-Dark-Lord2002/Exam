/* خروجی مثال‌ها، تمرین‌ها و آزمون فصل ۴ برنامه‌سازی (بازگشت).
   اجرا:  gcc -std=c11 -w "فصل-04.c" -o f4 && ./f4 */
#include <stdio.h>
void p1(int n) { if (n == 0) return; printf("%d ", n); p1(n - 1); }
void q1(int n) { if (n == 0) return; q1(n - 1); printf("%d ", n); }
void r1(int n) { if (n <= 0) return; printf("%d ", n); r1(n - 2); printf("%d ", n); }
int calls = 0;
int fibc(int n) { calls++; if (n < 2) return n; return fibc(n - 1) + fibc(n - 2); }
int dsum(int n) { if (n == 0) return 0; return n % 10 + dsum(n / 10); }
void bin(int n) { if (n > 1) bin(n / 2); printf("%d", n % 2); }
long hanoi(int n) { return n == 0 ? 0 : 2 * hanoi(n - 1) + 1; }
int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
int pw(int x, int n) { if (n == 0) return 1; int t = pw(x, n / 2); return n % 2 ? t * t * x : t * t; }
/* آزمون */
int t1(int n) { if (n <= 0) return 0; return n + t1(n - 2); }
void t2(int n) { if (n > 0) { t2(n - 1); printf("%d", n); t2(n - 1); } }
int c3 = 0;
int t3(int n) { c3++; if (n < 2) return n; return t3(n - 1) + t3(n - 2); }
int t4(int x) { if (x > 100) return x - 10; return t4(t4(x + 11)); }
int t5(int n) { static int k = 0; k += n; if (n > 1) t5(n - 1); return k; }
int t6(int n) { if (n == 1) return 1; if (n % 2 == 0) return t6(n / 2); return t6(3 * n + 1) + 1; }
void t7(const char *s) { if (*s) { t7(s + 1); putchar(*s); } }
int t8(int a, int b) { if (b == 0) return 0; if (b % 2 == 0) return t8(a + a, b / 2); return t8(a + a, b / 2) + a; }
int c9 = 0;
int t9(int n) { c9++; if (n <= 1) return 1; return t9(n / 2) + t9(n / 2); }
int t10(int n, int acc) { return n == 0 ? acc : t10(n / 10, acc * 10 + n % 10); }
int main(void) {
  printf("E1: "); p1(3); printf("\nE2: "); q1(3); printf("\nE3: "); r1(5); printf("\n");
  calls = 0; int v = fibc(5); printf("E4: fib(5)=%d calls=%d\n", v, calls);
  printf("E5: %d\nE6: ", dsum(1234)); bin(13); printf("\nE7: %ld %d %d\n", hanoi(5), gcd(48, 18), pw(2, 10));
  printf("Q1: %d\n", t1(7));
  printf("Q2: "); t2(3); printf("\n");
  int f6 = t3(6); printf("Q3: %d %d\n", f6, c3);
  printf("Q4: %d\n", t4(95));
  printf("Q5: %d\n", t5(4));
  printf("Q6: %d\n", t6(6));
  printf("Q7: "); t7("abc"); printf("\n");
  printf("Q8: %d\n", t8(7, 6));
  int h = t9(8); printf("Q9: %d %d\n", h, c9);
  printf("Q10: %d\n", t10(1203, 0));
  return 0;
}
