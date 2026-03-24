#include <iostream>
#include <openssl/rand.h>
#include <stdlib.h>
#include <random>

using namespace std;

int main(){


  int numberofReceivers =  2;
  std::cout << numberofReceivers << " Receivers" << endl;

  int numberofDataOwners = 5;
  std::cout << numberofDataOwners << " Data Owners" << endl;


  std::cout << "Data Preparation for the Beaver triplets Started" << endl;

  // choice vector
  int choice_vector[numberofDataOwners][numberofReceivers] = {}; 
  int choice_vector1[numberofDataOwners][numberofReceivers] = {}; 
  int choice_vector2[numberofDataOwners][numberofReceivers] = {}; 
 
 // sensitive data
  int data[numberofDataOwners][numberofReceivers] = {}; 
  int data1[numberofDataOwners][numberofReceivers] = {}; 
  int data2[numberofDataOwners][numberofReceivers] = {};  

  // random data for Beaver's triplets
  int alpha[numberofDataOwners][numberofReceivers] = {}; 
  int alpha1[numberofDataOwners][numberofReceivers] = {}; 
  int alpha2[numberofDataOwners][numberofReceivers] = {};

  int beta[numberofDataOwners][numberofReceivers] = {}; 
  int beta1[numberofDataOwners][numberofReceivers] = {}; 
  int beta2[numberofDataOwners][numberofReceivers] = {};

  int gamma[numberofDataOwners][numberofReceivers] = {}; 
  int gamma1[numberofDataOwners][numberofReceivers] = {}; 
  int gamma2[numberofDataOwners][numberofReceivers] = {};

  int epsilon[numberofDataOwners][numberofReceivers] = {}; 
  int epsilon1[numberofDataOwners][numberofReceivers] = {}; 
  int epsilon2[numberofDataOwners][numberofReceivers] = {}; 

  int delta[numberofDataOwners][numberofReceivers] = {}; 
  int delta1[numberofDataOwners][numberofReceivers] = {}; 
  int delta2[numberofDataOwners][numberofReceivers] = {}; 

  int partialAdd[numberofDataOwners][numberofReceivers] = {}; 
  int partialAdd1[numberofDataOwners][numberofReceivers] = {}; 
  int partialAdd2[numberofDataOwners][numberofReceivers] = {}; 

  int result[numberofDataOwners][numberofReceivers] = {}; 


  int Modulus = 32771; //32771>2^15 // Modulus should be a prime number

  // for random numbers
  std::random_device rd;
  std::uniform_int_distribution<long> dist;


  for(int i=0; i<numberofDataOwners; i++){
    for(int j=0; j<numberofReceivers; j++){

      // choosing Receivers for each DO
      choice_vector[i][j] = dist(rd) % 2;
      //std::cout << "random number for choice: " << choice_vector[i][j] << endl;

      choice_vector1[i][j] = dist(rd) % Modulus;
      //std::cout << "random share 1 for choice: " << choice_vector1[i][j] << endl;

      choice_vector2[i][j] = choice_vector[i][j] - choice_vector1[i][j];
      //std::cout << "random share 2 for choice: " << choice_vector2[i][j] << endl;


      // data of each DO
      if(choice_vector[i][j] == 1)
      data[i][j] = 36; 
      else
      data[i][j] = dist(rd) % Modulus;
      //std::cout << "data: " << i << j << "\t" << data[i][j] << endl;

      data1[i][j] = dist(rd) % Modulus;
      //std::cout << "random share 1 of data: " << data1[i][j] << endl;

      data2[i][j] = data[i][j] - data1[i][j];
      //std::cout << "random share 1 of data: " << data2[i][j] << endl;


      // generating alpha
      alpha[i][j] = dist(rd) % Modulus;
      //std::cout << "alpha: " << alpha[i][j] << endl;

      alpha1[i][j] = dist(rd) % Modulus;
      //std::cout << "random share 1 of alpha: " << alpha1[i][j] << endl;

      alpha2[i][j] = alpha[i][j] - alpha1[i][j];
      //std::cout << "random share 1 of alpha: " << alpha2[i][j] << endl;


      // generating beta
      beta[i][j] = dist(rd) % Modulus;
      //std::cout << "beta: " << beta[i][j] << endl;

      beta1[i][j] = dist(rd) % Modulus;
      //std::cout << "random share 1 of beta: " << beta1[i][j] << endl;

      beta2[i][j] = beta[i][j] - beta1[i][j];
      //std::cout << "random share 1 of beta: " << beta2[i][j] << endl;

    
      //constracting gamma and its shares
      gamma[i][j] = (alpha[i][j]) * (beta[i][j]);
      //std::cout << "gamma: " << gamma[i][j] << endl;

      gamma1[i][j] = dist(rd) % Modulus;
      //std::cout << "random share 1 of gamma: " << gamma1[i][j] << endl;

      gamma2[i][j] = gamma[i][j] - gamma1[i][j];
      //std::cout << "random share 1 of gamma: " << gamma2[i][j] << endl; 
    }
  }

  std::cout << "Data Preparation for the Beaver triplets Done" << endl;




  std::cout << "Learning authorised Receivers Started" << endl;

  int authorisedRj[numberofReceivers] = {};
  int authorisedRj1[numberofReceivers] = {};
  int authorisedRj2[numberofReceivers] = {};


  //  Agg - the addition of shared choice vector1

  for (int j = 0; j < numberofReceivers; ++j){
    for (int i = 0; i < numberofDataOwners; ++i){
     authorisedRj1[j] += choice_vector1[i][j];
   } 
  }


  // Dec - the addition of shared choice vector2  
  
  for (int j = 0; j < numberofReceivers; ++j){
    for (int i = 0; i < numberofDataOwners; ++i){
     authorisedRj2[j] += choice_vector2[i][j];
   } 
  }

  std::cout << "Learning authorised Receivers by Agg and Dec Started" << endl;  


  // Agg and Dec compute the number of DOs for Rj
  for (int j = 0; j < numberofReceivers; ++j){
    authorisedRj[j] = authorisedRj1[j] + authorisedRj2[j];
  }


  int t = 0;
  int min = authorisedRj[0];
  int max = authorisedRj[0];

  // automatic deciding t
  for(int i=1; i<numberofReceivers; i++)
    {
    // If current element is greater than max
        if(authorisedRj[i] > max)
            max = authorisedRj[i];
        // If current element is smaller than min
        if(authorisedRj[i] < min)
            min = authorisedRj[i];
    }

  t = (min + max) / 2; 
  //std::cout << "min t: " << min << endl;
  //std::cout << "max t: " << max << endl;
  std::cout << "threshold t:"<< "\t" << t << endl;

  int dataAggforAuthorisedRj[numberofReceivers] = {};


  for (int i = 0; i < numberofReceivers; ++i)
  {
     if (authorisedRj[i] >= t)
     {
       dataAggforAuthorisedRj[i] = 1;
       //std:: cout << " Authorised R[" << i <<"] has " << authorisedRj[i] << " votes" << endl;
     }
  }

  std::cout << "Learning authorised Receivers Done" << endl;


  std::cout << "Aggregation Started" << endl; 


	for (int i = 0; i < numberofDataOwners; ++i){
	    for (int j = 0; j < numberofReceivers; ++j){
	      if (dataAggforAuthorisedRj[j]==1){
	        ////////////////
	        //by Agg
	        //////////////// 
	      	epsilon1[i][j]= data1[i][j] + alpha1[i][j];
	      	delta1[i][j] = choice_vector1[i][j] + beta1[i][j];

	        ////////////////
	        // by Dec
	        ////////////////
	        epsilon2[i][j]= data2[i][j] + alpha2[i][j];
	      	delta2[i][j] = choice_vector2[i][j] + beta2[i][j];

	        ////////////////
	        // both
	        ////////////////
	        epsilon[i][j] = epsilon1[i][j] + epsilon2[i][j];
	        delta[i][j] = delta1[i][j] + delta2[i][j]; 

	        ////////////////
	        //by Agg
	        //////////////// 
	        partialAdd1[i][j] = gamma1[i][j] + epsilon[i][j]*choice_vector1[i][j]+delta[i][j]*data1[i][j];

	        ////////////////
	        // by Dec
	        ////////////////
	       	partialAdd2[i][j] = gamma2[i][j] + epsilon[i][j]*choice_vector2[i][j]+delta[i][j]*data2[i][j];

	        ////////////////
	        // by Dec
	        ////////////////
	        partialAdd[i][j] = partialAdd1[i][j] + partialAdd2[i][j];
	        result[i][j] = partialAdd[i][j] - epsilon[i][j]*delta[i][j];

		    }
		}
	}

  int AggforRj[numberofReceivers] = {0};

  for (int i = 0; i < numberofReceivers; ++i){
    //std::cout << "error inside for1" << endl;
    if (dataAggforAuthorisedRj[i]==1){
      //std::cout << "error inside if" << endl;  
      for (int j = 0; j < numberofDataOwners; ++j){
        //std::cout << "error inside for2" << endl;
        AggforRj[i] += result[j][i];
        //std::cout << "error"<< i << j << endl;
      }
    }
  }



	for (int i = 0; i < numberofReceivers; ++i){
		if (dataAggforAuthorisedRj[i]==1){
			std::cout << "Authorised R["<< i <<"] has " << authorisedRj[i] << " votes. Resulting Data Aggregation is:" << "\t" << AggforRj[i] % Modulus << endl;
		}
	}










  std::cout << "Aggregation Done" << endl; 








	return 0;
}