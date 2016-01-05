int main()
{
  int a[3] = {1, 2, 3};
  int b_0 = 5, b_1 = 6, b_2 = 7, b_r = 8;
  int *b[3] = {&b_0, &b_1, &b_2};

  if(a[0] != 1) return 1;
  if(a[1] != 2) return 2;
  if(a[2] != 3) return 3;

  if(*b[0] != 5) return 4;
  if(*b[1] != 6) return 5;
  if(*b[2] != 7) return 6;

  a[1] = 5;
  if(a[1] != 5) return 7;
  if(a[0] + a[1] + a[2] != 9) return 8;

  b[0] = &b_r;
  if(*b[0] != 8) return 9;

  a[2] += 3;
  if(a[2] != 6) return 10;
  a[2] -= 3;
  if(a[2] != 3) return 11;
  a[2]++;
  if(a[2] != 4) return 12;
  a[2]--;
  if(a[2] != 3) return 13;
  ++a[2];
  if(a[2] != 4) return 14;
  --a[2];
  if(a[2] != 3) return 15;

  b[1]++;
  if(b[1] - &b_1 != 1) return 16;

  if(&b[2] - &b[0] != 2) return 17;

  return 0;
}
