module Api
  module V1
    class MembersController < BaseController
      before_action :set_member, only: %i[show update destroy]

      def index
        members = current_user.members.active.order(:name)
        render json: members
      end

      def show
        render json: @member
      end

      def create
        member = current_user.members.build(member_params)
        if member.save
          render json: member, status: :created
        else
          render json: { errors: member.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @member.update(member_params)
          render json: @member
        else
          render json: { errors: @member.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @member.update!(active: false)
        head :no_content
      end

      private

      def set_member
        @member = current_user.members.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Portador não encontrado", status: :not_found)
      end

      def member_params
        params.permit(:name, :relationship)
      end
    end
  end
end
