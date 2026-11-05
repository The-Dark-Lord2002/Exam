/* خروجی مثال‌ها، تمرین‌ها و آزمون فصل ۶ برنامه‌سازی (struct، union، حافظهٔ پویا، لیست پیوندی).
   اجرا:  gcc -std=c11 -w "فصل-06.c" -o f6 && ./f6 */
#include <stdio.h>
#include <stdlib.h>
struct P { int x, y; };
void mv(struct P p) { p.x = 100; }
void mv2(struct P *p) { p->x = 100; }
struct S { char c; int i; char d; };
struct T { int i; char c; char d; };
struct D { char c; double d; };
union U { int i; char c[8]; };
struct A { int v[3]; };
struct node { int v; struct node *next; };
struct node *push(struct node *h, int v) { struct node *n = malloc(sizeof *n); n->v = v; n->next = h; return n; }
int count(struct node *h) { return h ? 1 + count(h->next) : 0; }
struct node *rev(struct node *h) { struct node *prev = NULL; while (h) { struct node *nx = h->next; h->next = prev; prev = h; h = nx; } return prev; }
int main(void) {
  { struct P a = {1, 2}, b; b = a; b.x = 9; printf("Q1: %d %d\n", a.x, b.x); }
  { struct P a = {1, 2}; mv(a); printf("Q2: %d ", a.x); mv2(&a); printf("%d\n", a.x); }
  printf("Q3: %zu\nQ4: %zu\nQ5: %zu\nE-D: %zu\n", sizeof(struct S), sizeof(struct T), sizeof(union U), sizeof(struct D));
  { int *p = calloc(4, sizeof(int)); p[1] = 5; printf("Q6: %d\n", p[0] + p[1] + p[3]); free(p); }
  { struct node *h = NULL; h = push(h, 1); h = push(h, 2); h = push(h, 3); printf("Q7: "); for (struct node *t = h; t; t = t->next) printf("%d ", t->v); printf("| count=%d | rev: ", count(h)); h = rev(h); for (struct node *t = h; t; t = t->next) printf("%d ", t->v); printf("\n"); }
  { struct A a = {{1, 2, 3}}, b = a; b.v[0] = 9; printf("Q8: %d %d\n", a.v[0], b.v[0]); }
  { struct P arr[3] = {{1,2},{3,4},{5,6}}; struct P *p = arr; p++; printf("Q9: %d %d\n", p->y, (p + 1)->x); }
  { int *p = malloc(3 * sizeof(int)); for (int i = 0; i < 3; i++) p[i] = i * i; p = realloc(p, 5 * sizeof(int)); p[4] = 7; printf("Q10: %d %d\n", p[2], p[4]); free(p); }
  return 0;
}
