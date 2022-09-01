from spartid_ais import kystverket


class TestReceive:
    def test_error(self):
        msg = kystverket.read_raw("a")
        assert msg is None

    def test_msg_3_postion_report(self):
        raw = [
            "\\s:2573535,c:1601581333*05\\!BSVDM,1,1,,A,33mGpL5000QE5URWuPIIj9LL0Dg:,0*02\r"  # noqa: E501
        ]
        msg = kystverket.read_raw(raw)
        print(msg)
        assert msg["id"] == 3
        assert msg["mmsi"] == 257292400
        assert msg["true_heading"] == 302
        assert 250 < msg["cog"] < 251
        assert 69 < msg["y"] < 70
        assert 18 < msg["x"] < 19
        assert msg["position_accuracy"] == 1

    def test_msg_1_postion_report(self):
        raw = [
            "\\s:2573515,c:1601654238*06\\!BSVDM,1,1,,A,13mdit?P00Q>HhRWL76v4?vT20S?,0*70\r"  # noqa: E501
        ]
        msg = kystverket.read_raw(raw)
        print(msg)
        assert msg["id"] == 1
        assert msg["mmsi"] == 257634800
        assert msg["true_heading"] == 511
        #        assert 250 < msg['cog'] < 251
        assert 68 < msg["y"] < 69
        assert 17 < msg["x"] < 18
        assert msg["position_accuracy"] == 1

    def test_4_base_station_report(self):
        raw = [
            "\\s:2573010,c:1601654238*06\\!BSVDM,2,1,2,B,53m?QB400000hE9<000P4q>0985AA=A8tl00000Q10A346O@050QDQiCP000,0*01\r",  # noqa: E501
            "\\s:2573010,c:1601654238*06\\!BSVDM,2,2,2,B,00000000000,2*3C\r",
        ]
        msg = kystverket.read_raw(raw)
        print(msg)
        assert msg["id"] == 5
        assert msg["mmsi"] == 257155400
        assert "HANS BRATTSTROM" in msg["name"]
        assert "LERS" in msg["callsign"]
        assert "BERGEN" in msg["destination"]


class TestProblemMessages:
    def test_bad_bit_count(self):
        raw = [
            "\s:2573575,c:1601669415*07\!BSVDM,1,1,,B,H3mfmU0l4LqE<00000000000000,2*5A"  # noqa: E501,W605
        ]
        msg = kystverket.read_raw(raw)
        assert msg["id"] == 3
        assert msg["mmsi"] == 1
        assert 0 == 1
