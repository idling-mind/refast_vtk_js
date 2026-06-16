from refast_vtk_js import ThresholdPoints

def test_threshold_points_basic():
    # Test single criteria dictionary initialization (should be wrapped in a list)
    criteria = {
        "array_name": "sine wave",
        "field_association": "PointData",
        "operation": "Above",
        "value": 30.0,
    }
    
    comp = ThresholdPoints(criterias=criteria)
    result = comp.render()
    
    assert result["type"] == "VtkThresholdPoints"
    assert result["props"]["criterias"] == [criteria]
    assert result["props"]["port"] == 0

def test_threshold_points_multiple():
    # Test multiple criteria list initialization
    criterias = [
        {
            "array_name": "x",
            "field_association": "Points",
            "operation": "Above",
            "value": -0.5,
        },
        {
            "array_name": "x",
            "field_association": "Points",
            "operation": "Below",
            "value": 0.5,
        }
    ]
    
    comp = ThresholdPoints(criterias=criterias, port=1)
    result = comp.render()
    
    assert result["type"] == "VtkThresholdPoints"
    assert result["props"]["criterias"] == criterias
    assert result["props"]["port"] == 1

def test_threshold_points_with_children():
    # Test adding children to the component via constructor
    comp = ThresholdPoints(criterias=[], children=["child_node"])
    result = comp.render()
    
    assert result["children"] == ["child_node"]
