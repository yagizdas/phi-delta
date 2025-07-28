import wolframalpha, httpx, xmltodict

# wolfram tool had problems with async Client.aquery so we monkey-patched it to use httpx.AsyncClient instead
# BEWARE: totally AI generated function.
async def tolerant_aquery(self, input, params=(), **kw):
    """Replacement for Client.aquery
       • ignores obsolete Content-Type assert
       • returns a proper wolframalpha.Result object whose pods are Pod instances
    """
    async with httpx.AsyncClient() as cli:
        resp = await cli.get(
            self.url,
            params={**dict(params), "appid": self.app_id, "input": input, **kw},
        )

    # Accept any XML-ish MIME type
    if "xml" not in resp.headers.get("Content-Type", "").lower():
        raise RuntimeError(f"Unexpected Content-Type: {resp.headers.get('Content-Type')}")

    # Parse to rich objects (Pod, Subpod, etc.)
    data = xmltodict.parse(resp.content,
                           postprocessor=wolframalpha.Document.make)

    # Normal success → <queryresult …>; quota/key problems → <error …>
    qr_dict = data.get("queryresult") or {"error": data.get("error", {"msg": "Unknown error"})}

    return wolframalpha.Result(qr_dict)

from langchain_community.utilities import WolframAlphaAPIWrapper
from pd_secrets import WOLFRAM_ALPHA_APPID

def run_wolfram_alpha_query(query:str):
    """Runs a Wolfram Alpha query using the provided query string.
    Args:
        query (str): The query string to send to Wolfram Alpha.
    Returns:
        str: The response from Wolfram Alpha.
    """
    wolframalpha.Client.aquery = tolerant_aquery

    api = WolframAlphaAPIWrapper(wolfram_alpha_appid=WOLFRAM_ALPHA_APPID)

    return api.run(query)

