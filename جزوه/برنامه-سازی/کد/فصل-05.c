/* خروجی مثال‌ها، تمرین‌ها و آزمون فصل ۵ برنامه‌سازی (اشاره‌گر، آرایه، رشته).
   اجرا:  gcc -std=c11 -w "فصل-05.c" -o f5 && ./f5 */
#include <stdio.h>
#include <string.h>
void f5(int *x, int y) { *x += y; y += *x; }
int len(const char *s) { const char *t = s; while (*t) t++; return t - s; }
int main(void) {
  { int a[] = {10, 20, 30, 40}; int *p = a; printf("E1: %d %d %d %d\n", *p + 1, *(p + 1), p[3], 2[a]); }
  { int a[] = {10, 20, 30}; int *p = a; int x = *p++; printf("E2: %d %d ", x, *p); int y = (*p)++; printf("%d %d ", y, a[1]); int z = ++*p; printf("%d %d\n", z, a[1]); }
  { int a[5]; int *p = &a[1], *q = &a[4]; printf("E3: %ld\n", (long)(q - p)); }
  { char s[] = "hello"; char *t = "hello"; printf("E4: %zu %zu %zu\n", sizeof(s), strlen(s), sizeof(t)); }
  { int b[3][4] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}}; printf("E5: %d %d %zu %zu\n", *(*(b + 1) + 2), *(b[2] + 1), sizeof(b), sizeof(b[0])); }
  { char s[] = "abcdef"; char *p = s + 2; printf("E6: %s %c\n", p, *(p + 2)); }
  { int x = 5; int *p = &x; int **pp = &p; **pp = 9; printf("E7: %d\n", x); }
  { printf("E8: %d %d\n", len("kankur"), strcmp("abc", "abd") < 0); }
  /* آزمون */
  { int a[] = {1, 2, 3, 4, 5}; int *p = a + 1; p += 2; printf("Q1: %d %ld\n", *p, (long)(p - a)); }
  { int a[] = {5, 10, 15}; int *p = a; *p++ += 1; printf("Q2: %d %d\n", a[0], *p); }
  { char s[] = "computer"; printf("Q3: %c%c%c\n", *s, *(s + 3), s[strlen(s) - 1]); }
  { int m[2][3] = {{1,2,3},{4,5,6}}; int *p = &m[0][0]; printf("Q4: %d %d\n", *(p + 4), m[1][0] + *(*m + 2)); }
  { int a = 2, b = 3; f5(&a, b); printf("Q5: %d %d\n", a, b); }
  { char *p = "abcde"; p += 2; printf("Q6: %s %zu\n", p, strlen(p)); }
  { int a[] = {10, 20, 30}; int *p = a; printf("Q7: %d\n", *(p + 1) + *p + 1); }
  { int a[10]; int *p = a; printf("Q8: %zu %zu\n", sizeof(a) / sizeof(a[0]), sizeof(p)); }
  { char s[10] = "ab"; strcat(s, "cd"); printf("Q9: %s %zu %zu\n", s, strlen(s), sizeof(s)); }
  { int x = 1, y = 2; int *p = &x, *q = &y; *p = *q + 1; p = q; *p = 7; printf("Q10: %d %d\n", x, y); }
  return 0;
}
