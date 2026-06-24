from refast_vtk_js import ThresholdPoints, Annotation, Annotations

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


def test_annotation_basic():
    comp = Annotation(position=[1.0, 2.0, 3.0], children=["hello label"])
    result = comp.render()

    assert result["type"] == "VtkAnnotation"
    assert result["props"]["position"] == [1.0, 2.0, 3.0]
    assert result["children"] == ["hello label"]


def test_annotation_extended():
    class MockCallback:
        def serialize(self):
            return {"callbackId": "drag-cb-id"}

    comp = Annotation(
        position=[1.0, 2.0, 3.0],
        card_position=[1.5, 2.5, 3.5],
        show_line=True,
        line_color="#ff0000",
        line_width=2.5,
        draggable=True,
        on_card_position_change=MockCallback(),
        anchor="top-left",
        bg_color="rgba(100, 100, 100, 0.5)",
    )
    result = comp.render()

    assert result["props"]["card_position"] == [1.5, 2.5, 3.5]
    assert result["props"]["show_line"] is True
    assert result["props"]["line_color"] == "#ff0000"
    assert result["props"]["line_width"] == 2.5
    assert result["props"]["draggable"] is True
    assert result["props"]["on_card_position_change"] == {"callbackId": "drag-cb-id"}
    assert result["props"]["anchor"] == "top-left"
    assert result["props"]["bg_color"] == "rgba(100, 100, 100, 0.5)"



def test_annotations_basic():
    items = [{"position": [1.0, 2.0, 3.0], "text": "hello"}]
    comp = Annotations(items=items)
    result = comp.render()

    assert result["type"] == "VtkAnnotations"
    assert result["props"]["items"] == items


def test_annotations_extended():
    class MockCallback:
        def serialize(self):
            return {"callbackId": "drag-cb-id-plural"}

    items = [
        {
            "position": [1.0, 2.0, 3.0],
            "card_position": [1.5, 2.5, 3.5],
            "text": "hello",
            "color": "red",
            "bg_color": "blue",
            "anchor": "right-center",
        }
    ]
    comp = Annotations(
        items=items,
        show_line=True,
        line_color="#00ff00",
        line_width=3.0,
        draggable=True,
        on_card_position_change=MockCallback(),
        anchor="bottom-left",
    )
    result = comp.render()

    assert result["props"]["items"] == items
    assert result["props"]["show_line"] is True
    assert result["props"]["line_color"] == "#00ff00"
    assert result["props"]["line_width"] == 3.0
    assert result["props"]["draggable"] is True
    assert result["props"]["on_card_position_change"] == {"callbackId": "drag-cb-id-plural"}
    assert result["props"]["anchor"] == "bottom-left"
