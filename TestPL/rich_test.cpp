#include<iostream>
using namespace std;

int main(){
    int num = 8; //rich(num)
    int rich = 1; //declare the accumulator

    // where the action happens
    while(num > 1){ //loop through the input
        rich = rich * num; //calculate rich!
        num--; // find result
    }

//print the result
cout << "Rich = " << rich << endl; //print rich!
    return 0;
}
