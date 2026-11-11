#include <stdio.h>
int main(void){
  int x = 0;
  if (x > 0)
      printf("A");
      printf("B");
  printf("\n");
  int n = 75;
  if (n >= 90) printf("A");
  else if (n >= 70) printf("B");
  else printf("C");
  printf("\n");
  int s = 0, i;
  for (i = 1; i <= 4; i++) s += i;
  printf("%d %d\n", s, i);
  int k = 1; while (k < 20) k *= 3; printf("%d\n", k);
  return 0;
}
