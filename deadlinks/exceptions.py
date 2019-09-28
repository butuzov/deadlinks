# Copyright 2019 Oleg Butuzov. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class DeadlinksExeption(BaseException):
    pass


class DeadlinksSettings(DeadlinksExeption):
    pass


class DeadlinksSettinsBase(DeadlinksSettings):
    pass


class DeadlinksSettinsThreads(DeadlinksSettings):
    pass


class DeadlinksSettinsRetry(DeadlinksSettings):
    pass


class DeadlinksSettinsChange(DeadlinksSettings):
    pass


class DeadlinksSettinsDomain(DeadlinksSettings):
    pass


class DeadlinksSettinsPathes(DeadlinksSettings):
    pass
