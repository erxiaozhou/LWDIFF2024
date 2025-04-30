f32_can_func = '''
  (func $f32_can_func (param f32) (result f32)
    local.get 0  
    local.get 0
    f32.ne
    if  (result f32)      
        f32.const nan
    else
        local.get 0       
    end
  )
'''


f64_can_func = '''
  (func $f64_can_func (param f64) (result f64)
    local.get 0           
    local.get 0
    f64.ne
    if  (result f64)  
        f64.const nan
    else
        local.get 0   
    end
  )
'''
f32_4_can_func = '''
  (func $f32_4_can_func (param v128) (result v128)
  (local f32)
    local.get 0       
    local.get 0            
    f32x4.extract_lane 0   
    local.tee 1
    local.get 1
    f32.ne
    if  (result f32)       
        f32.const nan
    else
        local.get 1
    end
    f32x4.replace_lane 0
    
    local.get 0            
    f32x4.extract_lane 1  
    local.tee 1
    local.get 1
    f32.ne
    if  (result f32)      
        f32.const nan
    else
        local.get 1
    end
    f32x4.replace_lane 1
    
    local.get 0           
    f32x4.extract_lane 2  
    local.tee 1
    local.get 1
    f32.ne
    if  (result f32)      
        f32.const nan
    else
        local.get 1
    end
    f32x4.replace_lane 2
    
    local.get 0           
    f32x4.extract_lane 3  
    local.tee 1
    local.get 1
    f32.ne
    if  (result f32)          
        f32.const nan
    else
        local.get 1
    end
    f32x4.replace_lane 3
  )
'''

f64_2_can_func = '''
  (func $sum_simd (param v128) (result v128)
  (local f64)
    local.get 0              
    local.get 0              
    f64x2.extract_lane 0     
    local.tee 1
    local.get 1
    f64.ne
    if  (result f64)         
        f64.const nan
    else
        local.get 1
    end
    f64x2.replace_lane 0
    
    local.get 0              
    f64x2.extract_lane 1     
    local.tee 1
    local.get 1
    f64.ne
    if  (result f64) 
        f64.const nan
    else
        local.get 1
    end
    f64x2.replace_lane 1
  )
'''
pre_defined_func_code ={
  'can_f32': f32_can_func,
  'can_f64': f64_can_func,
  'can_f32x4': f32_4_can_func,
  'can_f64x2': f64_2_can_func
}