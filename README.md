<h1 align="center">💻 IPSE LMS: 차세대 AI 및 알고리즘 학술 동아리 학습 플랫폼</h1>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
</div>

<br>

## 📖 목차 (Table of Contents)

1. [프로젝트 개요](#-프로젝트-개요)
2. [주요 기능](#-주요-기능)
3. [시스템 아키텍처 및 기술 스택](#-시스템-아키텍처-및-기술-스택)
4. [팀원 및 역할](#-팀원-및-역할)

<br>

## 📌 프로젝트 개요

충북대학교 AI 및 알고리즘 학술 동아리 IPSE부원들의 체계적인 기술 성장을 돕기 위해 개발된 자체 학습 관리 시스템(LMS)입니다. 로드맵 기반 커리큘럼 구조를 벤치마킹하여 설계되었습니다. 단순한 동영상 시청을 넘어, 동아리 부원들이 능동적으로 목표를 설정하고 자신의 학습 진도를 추적하며, 최종적으로 온라인 컴파일러, IPCP 대회 기능 구현까지 자연스럽게 이어질 수 있는 '통합형 에듀테크 환경'을 구축하는 것을 목표로 합니다.

## ✨ 주요 기능

- 로드맵 기반 학습 커리큘럼 (Path & Unit): `course` 앱의 관계형 데이터베이스 모델링을 통해 '새싹 단계'부터 '심화 알고리즘/보안' 과정까지 트리(Tree) 형태의 체계적인 강의 구조를 제공합니다.
- 실시간 수강 진도 추적 (Progress Tracking): 커스텀 `UserCourseProgress` 모델을 도입하여 동아리 부원 개개인의 강의 이수 상태 및 최근 접속 위치를 메인 대시보드에서 직관적으로 확인할 수 있습니다.
- UI & 반응형 웹: 최신 `Tailwind CSS v4` 엔진과 `daisyUI` 컴포넌트를 JIT(Just-In-Time) 컴파일러 방식으로 연동하여, 개발자 친화적인 세련된 다크 모드 인터페이스를 제공합니다.
- 동아리 맞춤형 통합 대시보드**: 멘토(Lecturer)와 멘티(Student) 권한을 분리하고, 정규 세션(Semester) 일정 및 중요 공지사항(`NewsAndEvents`)을 한눈에 파악할 수 있는 중앙 집중형 뷰를 제공합니다.

## 🛠 시스템 아키텍처 및 기술 스택

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/1edfc415-8a34-4258-938b-feb0cb49a6a1" />


- Backend Framework: Python 3.12, Django 5.x
- Frontend UI/UX: Tailwind CSS (Node.js v20 환경 기반 빌드), HTML5/Django Templates
- Database: SQLite (개발 환경) -> PostgreSQL (배포 환경 전환 예정)
- Version Control & CI/CD: Git / GitHub, Docker (추후 컨테이너 오케스트레이션 도입 예정)

## 👥 팀원 및 역할

| 이름       | 담당 업무                       | 세부 역할                                                                                                                                                              |
| ---------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **박종은** | 아키텍처 설계 및 풀스택 개발 | 프로젝트 인프라 초기 세팅, 데이터베이스 구조 설계 (Custom User, Course, Progress), Tailwind CSS 기반의 프론트엔드 연동 및 GNB/대시보드 UI 구현, 깃허브 버전 관리 총괄 |
