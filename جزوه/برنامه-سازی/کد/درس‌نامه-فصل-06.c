#include <stdio.h>
#include <stdlib.h>
struct Student { int id; double avg; };
struct node { int v; struct node *next; };
struct node *push(struct node *h, int v){ struct node *n = malloc(sizeof *n); n->v=v; n->next=h; return n; }
int main(void){
  struct Student s = {7, 16.5};
  struct Student *p = &s;
  p->avg = 18;
  printf("%d %.1f %zu\n", s.id, s.avg, sizeof(struct Student));
  int n = 4; int *a = malloc(n * sizeof(int)); for (int i = 0; i < n; i++) a[i] = i * i;
  printf("%d %d\n", a[3], a[1]); free(a);
  struct node *h = NULL; h = push(h, 1); h = push(h, 2); h = push(h, 3);
  for (struct node *t = h; t; t = t->next) printf("%d ", t->v); printf("\n");
  return 0;
}
