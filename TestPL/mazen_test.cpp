#include <iostream>
using namespace std;

void func(char &maz1, char maz2){
  cout << "hi Mom!" << endl;
  maz1--;
  maz2++;
}

int main(){
  char mazen = 'a';
  mazen++;

  if(mazen == 'c') {
    cout << mazen;
  }

  if(mazen == 'b') {
    func(mazen, mazen);//, mazen2);
  }

  if(mazen == 'a') {
    cout << "hi Dad!" << endl;
  }

  return 0;
}
