#include <iostream>
using namespace std;

void func(char &b1){
  b1++;
  if (b1 <= 'f'){
    func(b1);
  }
}

int main(){
  char bidit='a';
  func(bidit);
  return 0;
}
