/* خروجی مثال‌های تکمیلی (جعبه‌های «مثال») در فصل ۱ تا ۶ برنامه‌سازی.
   شمارهٔ هر خط خروجی: ۱ تا ۱۰ فصل ۱ و ۲، ۱۱ تا ۱۳ فصل ۳، ۱۴ تا ۱۸ فصل ۴، ۱۹ تا ۲۳ و ۲۸ فصل ۵، ۲۴ تا ۲۷ فصل ۶.
   اجرا:  gcc -std=c11 -w "مثال-ها.c" -o ex && ./ex */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define BADMAX(a,b) (a) > (b) ? (a) : (b)
int g_glob;
int sign(int x) { if (x < 0) return -1; if (x == 0) return 0; return 1; }
int calls;
int fib(int n){calls++; return n<2?n:fib(n-1)+fib(n-2);}
int h(int n){calls++; if(n<=1) return 1; return h(n/2)+h(n/2);}
int gcd(int a,int b){calls++; return b==0?a:gcd(b,a%b);}
long pw(long x,int n){calls++; if(n==0) return 1; long t=pw(x,n/2); return n%2? t*t*x : t*t;}
int fs(int n){ static int c=0; c++; if(n>0) fs(n-1); return c; }
int fact(int n){ return n<=1?1:n*fact(n-1); }
struct S { int a[3]; };
struct A1 { char c; short s; int i; };
struct A2 { double d; char c; };
union U { int i; char c[4]; };
int main(void){
  printf("1: %zu %zu %zu %zu %zu %zu\n", sizeof(char), sizeof(short), sizeof(int), sizeof(double), sizeof(0.1), sizeof(0.1f));
  char c='B'; printf("2: %c %d %c\n", c+1, c-'A', 'G'+32);
  int n=1234; printf("3: %d %d %d %d\n", 17/5, 17%5, n%10, n/10);
  printf("3b: %d\n", (-7/2)*2 + (-7%2));
  int i=3; int a=i++; int b=++i; printf("4: %d %d %d\n", a,b,i);
  int x=2; x -= 1+1; printf("5: %d\n", x);
  int r = 2 + 3 * 4 > 10 && !0; printf("6: %d %d\n", r, 10-4-3);
  int p1,p2; p1=p2=5; printf("6b: %d %d\n",p1,p2);
  int s7=7,t2=2; double av=(double)s7/t2, av2=s7/t2; printf("7: %.1f %.1f %d\n", av, av2, (int)3.99);
  if(-3) printf("8:A"); if(0) printf("B"); if(5>9); printf("C\n");
  for(int k=0;k<3;k++) printf("%d",k); int j=5; while(j<3) printf("X"); int k2=5; do printf("Y"); while(k2<3); printf("\n");
  int cnt=0,ii; for(ii=2; ii<=20; ii+=5) cnt++; printf("9: %d %d\n", cnt, ii);
  int q,w; for(q=0,w=10; q<w; q+=2,w-=3) printf("%d,%d ",q,w); printf("\n");
  unsigned u=2; int guard=0; for(; u>=0 && guard<5; u--, guard++) printf("%u ",u); printf("\n");
  char ch='e'; switch(ch){case 'a': case 'e': case 'i': case 'o': case 'u': printf("10: vowel\n"); break; default: printf("10: consonant\n");}
  printf("11: %d %d %d\n", sign(-7), sign(0), sign(4));
  static int st; printf("12: %d %d\n", g_glob, st);
  printf("13: %d %d\n", 2*MAX(2,3), 2*BADMAX(2,3));
  calls=0; fib(4); printf("14: fib4 calls %d\n", calls);
  calls=0; h(4); printf("15: h4 calls %d\n", calls);
  calls=0; gcd(48,18); printf("16: gcd calls %d\n", calls);
  calls=0; long v=pw(2,10); printf("17: pw %ld calls %d\n", v, calls);
  printf("18: %d\n", fs(3));
  printf("18b: %d\n", fact(3));
  int xx=5; int *pp=&xx; *pp=7; int **ppp=&pp; printf("19: %d ", xx); **ppp=9; printf("%d\n", xx);
  int arr[7]; printf("20: %zu\n", sizeof(arr)/sizeof(arr[0]));
  int bb[3][4]={{1,2,3,4},{5,6,7,8},{9,10,11,12}}; int *pb=&bb[0][0]; printf("21: %d %ld\n", *(pb+5), (long)((char*)&bb[2][1]-(char*)bb));
  char s10[10]="hi"; printf("22: %zu %zu\n", sizeof(s10), strlen(s10));
  printf("23: %d %d %d\n", strcmp("abc","abd")<0, strcmp("b","abc")>0, strcmp("ab","abc")<0);
  struct S s1={{1,2,3}}, s2; s2=s1; s2.a[0]=9; printf("24: %d %d\n", s1.a[0], s2.a[0]);
  printf("25: %zu %zu %zu\n", sizeof(struct A1), sizeof(struct A2), sizeof(union U));
  union U un; un.i=0x41424344; printf("26: %c\n", un.c[0]);
  int *cp=calloc(3,sizeof(int)); printf("27: %d %d %d ", cp[0],cp[1],cp[2]); cp[0]=4; cp=realloc(cp,5*sizeof(int)); printf("%d\n", cp[0]); free(cp);
  double dd[3]; printf("28: %ld\n", (long)((char*)(dd+1)-(char*)dd));
  return 0;
}
