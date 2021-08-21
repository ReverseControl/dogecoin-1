// Copyright (c) 2021 The Dogecoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

//Here be dragons, wizards, witches and master of the dark arts. 
//Careful thou who wonders 'round these parts without magic spells,
//mana potions and doggy treats...especially magical doggy treats.


//Only define this header on x86
#if ( defined(i386)     || defined(__i386)  || defined(__i386__) || \
      defined( __386)   || defined(_X86_)   || defined( _M_I86)  || \
      defined(__i386__) || defined(__X86__) || defined(__x86_64) ) 

    #ifndef LOWLEVEL_H
        #define LOWLEVEL_H
        
        #ifdef _WIN32
            #define __NT__
            #include <intrin.h>
        #else
            #include <x86intrin.h>
        #endif
        
        #include <cpuid.h>
        
        /* \union Useful for buffers that will need to be hashed
         *        where data gather comes from different int types.       
         */
        union block_512bits {
            char                    byte[64];
            unsigned char           ubyte[64];
            uint16_t                word[32];
            uint32_t                dword[16];
            uint64_t                qword[8];
            unsigned long long int  ulli[8]; 
        };
        
    #endif  /*LOWLEVEL_H*/
#endif  /*Detect x86*/
