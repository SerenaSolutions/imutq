// SPDX-License-Identifier: Apache-2.0
// SHA3-256 em JS puro (Keccak-f[1600]). WebCrypto nao oferece SHA3 no Chrome.
const RC = [1n,0x8082n,0x800000000000808an,0x8000000080008000n,0x808bn,0x80000001n,
  0x8000000080008081n,0x8000000000008009n,0x8an,0x88n,0x80008009n,0x8000000an,
  0x8000808bn,0x800000000000008bn,0x8000000000008089n,0x8000000000008003n,
  0x8000000000008002n,0x8000000000000080n,0x800an,0x800000008000000an,
  0x8000000080008081n,0x8000000000008080n,0x80000001n,0x8000000080008008n];
const R = [[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]];
const M = (1n<<64n)-1n;
const rot = (x,n)=> n===0?x: ((x<<BigInt(n))|(x>>BigInt(64-n)))&M;
function keccakF(A){
  for(let round=0; round<24; round++){
    const C=[0n,0n,0n,0n,0n];
    for(let x=0;x<5;x++) C[x]=A[x]^A[x+5]^A[x+10]^A[x+15]^A[x+20];
    for(let x=0;x<5;x++){ const D=C[(x+4)%5]^rot(C[(x+1)%5],1);
      for(let y=0;y<5;y++) A[x+5*y]^=D; }
    const B=new Array(25).fill(0n);
    for(let x=0;x<5;x++) for(let y=0;y<5;y++) B[y+5*((2*x+3*y)%5)]=rot(A[x+5*y],R[x][y]);
    for(let x=0;x<5;x++) for(let y=0;y<5;y++) A[x+5*y]=B[x+5*y]^((~B[(x+1)%5+5*y]&M)&B[(x+2)%5+5*y]);
    A[0]^=RC[round];
  }
  return A;
}
function sha3_256(input){
  const data = typeof input==="string" ? new TextEncoder().encode(input) : input;
  const rate=136, pad=rate;
  const msg=new Uint8Array(Math.ceil((data.length+1)/rate)*rate);
  msg.set(data); msg[data.length]^=0x06; msg[msg.length-1]^=0x80;
  const A=new Array(25).fill(0n);
  for(let off=0; off<msg.length; off+=rate){
    for(let i=0;i<rate/8;i++){
      let v=0n;
      for(let b=7;b>=0;b--) v=(v<<8n)|BigInt(msg[off+i*8+b]);
      A[i]^=v;
    }
    keccakF(A);
  }
  let hex="";
  for(let i=0;i<4;i++){ let v=A[i]; for(let b=0;b<8;b++){ hex+=Number(v&0xffn).toString(16).padStart(2,"0"); v>>=8n; } }
  return hex;
}
if (typeof module !== "undefined") module.exports = { sha3_256 };
