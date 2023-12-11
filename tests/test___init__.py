import pytest
import lasso.dyna as ld
import src.FEHMtools as functions

#initialize test inputs
test_plot=ld.D3plot("tests/d3plot")

test_part=ld.D3plot("tests/d3part")

#test brain_set function
def test_brain_set():
    #check first value in series
    result=functions.brain_set()
    assert result[0]==88000100
    
    #check positive and negative offsets
    result=functions.brain_set(offset=1)
    assert result[0]==88000101
    
    result=functions.brain_set(offset=-1)
    assert result[0]==88000099
    
    #check error for wrong offset input type
    with pytest.raises(TypeError):
        functions.brain_set(offset="one")
    
    
#test skull_set function
def test_skull_set():
    #check first value in series
    result_one, result_two=functions.skull_sets()
    
    assert result_one[0]==88000001
    assert result_two[0]==88000002
    
    #check positive and negative offsets
    result_one, result_two=functions.skull_sets(offset=1)
    
    assert result_one[0]==88000002
    assert result_two[0]==88000003
    
    result_one, result_two=functions.skull_sets(offset=1)
    
    assert result_one[0]==88000002
    assert result_two[0]==88000003
    
        #check error for wrong offset input type
    with pytest.raises(TypeError):
        functions.skull_sets(offset="one")
        
def test_element_part_ids():
    
    #check element indexes for d3plot
    test_solid_numbers=functions.element_part_ids(test_plot,format="solid")
    assert test_solid_numbers[0]==101
    assert test_solid_numbers[7]!=102
    assert test_solid_numbers[8]==102
    
    test_shell_numbers=functions.element_part_ids(test_plot,format="shell")
    assert test_shell_numbers[0]==201
    
    with pytest.raises(ValueError):
        functions.element_part_ids(test_plot,format=1.0)
    
    #check element indexes for d3plot
    test_solid_numbers=functions.element_part_ids(test_part)
    assert test_solid_numbers[0]==102
    assert test_solid_numbers[7]==102
    
    
