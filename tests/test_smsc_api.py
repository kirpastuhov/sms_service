import unittest
from unittest.mock import patch


class TestSmscApi(unittest.TestCase):
    async def test_request_smsc(self):
        with patch("src.smsc_api.request_smsc") as mocked_request:
            mocked_request.return_value = {"id": 457, "cnt": 1}
            mocked_resp = await mocked_request(
                "POST",
                "send",
                login="",
                password="",
                payload={"phones": [], "message": "", "valid_for": ""},
            )
            print(mocked_resp)

        mocked_request.assert_called_once_with(
            "POST",
            "send",
            login="",
            password="",
            payload={"phones": [], "message": "", "valid_for": ""},
        )
        self.assertEqual(mocked_resp, {"id": 457, "cnt": 1})

    # def test_split(self):
    #     s = "hello world"
    #     self.assertEqual(s.split(), ["hello", "world"])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__ == "__main__":
    unittest.main()
