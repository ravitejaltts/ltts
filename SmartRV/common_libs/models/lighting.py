from enum import Enum
from pydoc import describe
from typing import Optional, List, Union

from pydantic import BaseModel, Field


class LightOverview(BaseModel):
    title: str
    settings: dict
    switches: List[dict]


class LightBase(BaseModel):
    #category: str
    #code: str
    #instance: int
    onOff: int

    #def twin(self):
    #    return {self.category: {f'{self.code}{self.instance}': {'onOff': self.onOff}}}


class LightDim(LightBase):
    brt: Optional[int]

    dimming: Optional[int]  # for push button dimming
    # def twin(self):
    #     result = LightBase.twin(self)
    #     if self.brt is not None:
    #         result[self.category][f'{self.code}{self.instance}']['brt'] = self.brt
    #     return result


class LightRBGW(LightDim):
    rgb: str
    clrTmp: Optional[int]

    # def twin(self):
    #     result = LightDim.twin(self)
    #     result[self.category][f'{self.code}{self.instance}']['rgb'] = self.rgb
    #     if self.clrTmp is not None:
    #         result[self.category][f'{self.code}{self.instance}']['clrTmp'] = self.clrTmp
    #     return result


class LightDetail(BaseModel):
    title: str
    subtext: str

    type: str
    RGBW: Optional[LightRBGW]
    SIMPLE_ONOFF: Optional[LightBase]
    SIMPLE_DIM: Optional[LightDim]

    state: Optional[dict]

    masterState: Optional[dict]
    masterType: Optional[str]

    actions: List[str]
    action_default: Optional[dict]
    action_all: Optional[dict]

    zone_id: Optional[int]


class LightList(BaseModel):
    master: LightDetail
    lights: List[LightDetail]


class LightingUIResponse(BaseModel):
    overview: LightOverview
    lights: LightList


# if __name__ == '__main__':

#     light0 = LightBase(category="lighting",code="lz",instance=1,onOff=0)
#     print(f"light0 twin = {light0.twin()}")

#     light1 = LightDim(category="lighting",code="lz",instance=1,onOff=0,brt=100)
#     light2 = LightRBGW(category="lighting",code="lz",instance=2,onOff=0,brt=100,rgb="#00640064",clrTmp=90)

#     print(f"light1 twin = {light1.twin()}")
#     print(f"light2 twin = {light2.twin()}")
