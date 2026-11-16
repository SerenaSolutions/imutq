use metodo::*;
fn main(){
    for (a,n) in [(3u32,3u32),(8,10),(12,12),(16,16),(20,20),(20,25)] {
        println!("{a}/{n} -> limite {:.3} | {:?}", wilson_inferior(a,n,Z_95), decidir(a,n,0.80,8));
    }
    println!("faltam para 3/3: {}", respostas_faltantes(3,3,0.80,8));
}
